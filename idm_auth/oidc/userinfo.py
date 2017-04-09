def get_userinfo(claims, user):
    claims['sub'] = user.identity_id
