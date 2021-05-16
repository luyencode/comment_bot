# Chỉ kiểm duyệt các bình luận chưa được kiểm duyệt.
import datetime

USERNAME, ACCESS_TOKEN = open('access_token').read().split()
KEYWORD_FILE = 'keywords.txt'
HOME_API = "https://api.github.com"
REPO = "comments"
OWNER = "luyencode"
COUNT_LIMIT_RATE = 7
LATEST_SEE_COMMENT_TIME = '2021-05-16T03:54:21Z'
GITHUB_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
LATEST_SEE_COMMENT_TIME = datetime.datetime.strptime(LATEST_SEE_COMMENT_TIME, GITHUB_TIME_FORMAT)
ADMIN_ISSUE_ID = 279
TEMPLATE_SPOILER = """[**Thông báo**] Tài khoản @{} đã chia sẻ code (nhưng không ẩn) tại bài tập [{}](https://luyencode.net/problem/{}): Bình luận của bạn đã bị gỡ bỏ!

<details><summary>Nội dung đã đăng</summary>
<p>

{}

</p>
</details>

"""
TEMPLATE_DOCUMENT = "👉 Nhớ xem quy tắc & hướng dẫn [tại đây](https://gist.github.com/nguyenvanhieuvn/d3e5e20c44ef9d565fa3d7b9ebabfc65) nha cà nhà 😘"
