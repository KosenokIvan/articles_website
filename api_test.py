from requests import get, post, put, delete
from tools.image_to_byte_array import image_to_byte_array

'''register_response = post("http://localhost:5000/api/users", json={
    "name": "Razor",
    "surname": "Wolf",
    "nickname": "RazorWolf",
    "email": "razor@mail.mondstadt",
    "password": "q",
    "password_again": "q",
    "description": "Если вы это видите, регистрация при помощи API работает!!!",
    "avatar": image_to_byte_array("razor.png").hex()
})
print(register_response.json())
if not register_response:
    exit()

login_response = post("http://localhost:5000/api/login", json={
    "email": "razor@mail.mondstadt",
    "password": "q"
})
print(login_response.json())
if not login_response:
    exit()

article_response = post("http://localhost:5000/api/articles", json={
    "title": "Hello world!",
    "content": "Я успешно зарегистрировался и написал эту статью при помощи API!!!"
}, cookies=login_response.cookies)
print(article_response.json())'''

'''print(get("http://localhost:5000/api/users").json())'''

'''register_response = post("http://localhost:5000/api/users", json={
    "name": "TEST_NAME5",
    "surname": "TEST_SURNAME5",
    "nickname": "TestUser5",
    "email": "test_email5@test.test",
    "password": "q",
    "password_again": "q",
    "description": "Если вы это видите, регистрация при помощи API работает!!!",
    "avatar": image_to_byte_array("razor.png").hex()
})
print(register_response.json())
if not register_response:
    exit()'''

'''login_response = post("http://localhost:5000/api/login", json={
    "email": "test_email@test.test",
    "password": "qqqqqqqq"
})
print(login_response.json())
if not login_response:
    exit()

delete_response = delete("http://localhost:5000/api/user/5", cookies=login_response.cookies)
print(delete_response.json())'''

'''print(get("http://localhost:5000/api/articles"
          "?sorted_by=likes_count&get_field=id&get_field=title&author=4").json())
print(get("http://localhost:5000/api/users?nickname_search_string=ra&nickname_filter=starts").json())
print(get("http://localhost:5000/api/comment/4?get_field=image").json())'''

'''login_response = post("http://localhost:5000/api/login", json={
    "email": "razor@mail.wolvendom",
    "password": "qqqqqqqq"
})
print(login_response.json())
if not login_response:
    exit()

response = delete("http://localhost:5000/api/comment/8", cookies=login_response.cookies)
print(response.json())
'''
'''print(get("http://localhost:5000/api/user/2?get_field=name").json())
print(get("http://localhost:5000/api/like/36", cookies=login_response.cookies).json())
print(post("http://localhost:5000/api/like/36", cookies=login_response.cookies).json())
print(get("http://localhost:5000/api/like/36", cookies=login_response.cookies).json())
print(delete("http://localhost:5000/api/like/36", cookies=login_response.cookies).json())
print(get("http://localhost:5000/api/like/36").json())
print(post("http://localhost:5000/api/comments", json={
    "text": "No authorized",
    "article_id": 36
}).json())'''

"""print(post("http://localhost:5000/api/comments", cookies=login_response.cookies, json={
    "title": "q",
    "text": "q",
    "image": "h",
    "article_id": 36
}).json())"""

print(get("http://localhost:5000/api/users?sorted_by=nickname").json())
