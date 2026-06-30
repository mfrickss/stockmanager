from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import re


class JWTAuthenticationMiddleware:
    """
    Middleware que autentica o usuário via JWT armazenado em cookies HttpOnly.
    Substitui a SessionMiddleware + AuthenticationMiddleware para eliminar
    consultas ao banco de dados em cada requisição.
    
    Flow:
    1. Lê o cookie 'access_token'
    2. Se válido → popula request.user com o usuário do token
    3. Se expirado → tenta refresh automático via cookie 'refresh_token'
    4. Se nenhum token válido → request.user = AnonymousUser
    """

    # Rotas que NÃO precisam de autenticação
    PUBLIC_PATHS = [
        '/login/',
        '/admin/',
        '/static/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = AnonymousUser()
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        new_access_token = None

        if access_token:
            user = self._get_user_from_token(access_token)
            if user:
                request.user = user
            elif refresh_token:
                # Access token expirado, tenta refresh
                user, new_access_token = self._refresh_access_token(refresh_token)
                if user:
                    request.user = user

        elif refresh_token:
            # Sem access token, mas com refresh
            user, new_access_token = self._refresh_access_token(refresh_token)
            if user:
                request.user = user

        response = self.get_response(request)

        # Se fizemos refresh, seta o novo access token no cookie
        if new_access_token:
            response.set_cookie(
                'access_token',
                new_access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME_SECONDS', 1800),
            )

        return response

    def _get_user_from_token(self, token_str):
        """Valida o access token e retorna o User, sem consultar o banco."""
        try:
            token = AccessToken(token_str)
            user_id = token.get('user_id')
            username = token.get('username', '')
            
            # Criamos um objeto User "leve" populado a partir do JWT payload
            # Isso evita uma query ao banco em cada requisição
            user = User(pk=user_id, username=username)
            user._is_jwt_user = True
            return user
        except (TokenError, InvalidToken):
            return None

    def _refresh_access_token(self, refresh_token_str):
        """Tenta gerar um novo access token a partir do refresh token."""
        try:
            refresh = RefreshToken(refresh_token_str)
            user_id = refresh.get('user_id')
            username = refresh.get('username', '')

            # Gera novo access token com os claims customizados
            new_access = refresh.access_token
            new_access['username'] = username

            user = User(pk=user_id, username=username)
            user._is_jwt_user = True
            return user, str(new_access)
        except (TokenError, InvalidToken):
            return None, None
