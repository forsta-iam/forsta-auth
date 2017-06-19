def get_userinfo(claims, user):
    claims['sub'] = str(user.identity_id)
    return claims
