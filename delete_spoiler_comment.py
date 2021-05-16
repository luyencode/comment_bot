import datetime
import json
import re
import time
import traceback

import requests

import config

LATEST_COMMENT_TIME = config.LATEST_SEE_COMMENT_TIME
NEW_LATEST_COMMENT_TIME = LATEST_COMMENT_TIME

session = requests.Session()
session.auth = (config.USERNAME, config.ACCESS_TOKEN)
session.headers = {
    'accept': 'application/vnd.github.v3+json'
}

black_keys = set(open(config.KEYWORD_FILE).read().splitlines())


def handle_request(url, params=None, method='GET'):
    try:
        if method == 'GET':
            r = session.get(url=url, params=params)
        elif method == 'DELETE':
            r = session.delete(url=url, data=params)
        elif method == 'POST':
            r = session.post(url=url, data=params)
        if r.status_code == 403:
            print('Got Rate Limit Exceeded! Will try again...')
            time.sleep(3600)
            return handle_request(url, params)
        elif not r.ok:
            print('Got status_code', r.status_code)
        else:
            return r
    except:
        traceback.print_exc()
    return None


def get_all_issues():
    issue_urls = []
    page = 1
    URL = config.HOME_API + "/repos/{}/{}/issues".format(config.OWNER, config.REPO)
    while True:
        r = handle_request(URL, params={'sort': 'comments', 'direction': 'desc', 'page': page, 'per_page': 100})
        if r.status_code != 200:
            print(r.status_code, r.text)
            break
        resp = r.text
        page += 1
        issues = json.loads(resp)
        if len(issues) == 0:
            break
        for issue in issues:
            issue_urls.append(issue['url'])
    return issue_urls


def get_all_comment_from_issue(issue_url):
    comment_urls = []
    issue_url += '/comments'
    page = 1
    while True:
        r = handle_request(issue_url, params={'page': page, 'per_page': 100})
        if r.status_code != 200:
            print(r.status_code, r.text)
            break
        comments = json.loads(r.text)
        if len(comments) == 0:
            break
        page += 1
        for comment in comments:
            comment_urls.append(comment['url'])
    return comment_urls


def get_all_issue_comment_from_repo():
    comment_urls = []
    page = 1
    url = config.HOME_API + '/repos/{}/{}/issues/comments'.format(config.OWNER, config.REPO)
    while True:
        r = handle_request(url, params={'page': page, 'per_page': 100, 'direction': 'desc', 'sort': 'updated'})
        page += 1
        if r.status_code != 200:
            print(r.status_code, r.text)
            break
        comments = json.loads(r.text)
        if len(comments) == 0:
            break
        for comment in comments:
            global NEW_LATEST_COMMENT_TIME
            comment_time = datetime.datetime.strptime(comment['updated_at'], config.GITHUB_TIME_FORMAT)
            if comment_time > NEW_LATEST_COMMENT_TIME:
                NEW_LATEST_COMMENT_TIME = comment_time
            global LATEST_COMMENT_TIME
            if comment_time <= LATEST_COMMENT_TIME:
                break
            comment_urls.append(comment['url'])
    return comment_urls


def get_comment_detail(comment_url):
    r = handle_request(comment_url)
    return json.loads(r.text)


def is_spoiler_comment(body):
    count = 0
    for key in black_keys:
        count += body.count(key)
    if count > config.COUNT_LIMIT_RATE:
        if body.count('details') < 2 or body.count('/details') < 1 or \
                body.count('summary') < 2 or body.count('/summary') < 1 or \
                body.count('p') < 2 or body.count('/p') < 1 or \
                body.count('```') < 2:
            return True
        return False


def delete_comment(url):
    r = handle_request(url=url, method='DELETE')
    return r.status_code == 204


def make_issue_comment(issue_id, body):
    url = config.HOME_API + '/repos/{}/{}/issues/{}/comments'.format(config.OWNER, config.REPO, issue_id)
    r = handle_request(url, params=json.dumps({'body': body}), method='POST')
    return r.status_code == 201


def save_checkpoint():
    content = open('config.py').read()
    content = re.sub(r"LATEST_SEE_COMMENT_TIME = '[^']+",
                     r"LATEST_SEE_COMMENT_TIME = '" + NEW_LATEST_COMMENT_TIME.strftime(config.GITHUB_TIME_FORMAT),
                     content)
    with open('config.py', 'w') as wp:
        wp.write(content)


def get_problem_id(issue_id):
    url = config.HOME_API + '/repos/{}/{}/issues/{}'.format(config.OWNER, config.REPO, issue_id)
    r = handle_request(url)
    body = json.loads(r.text)['body'].split('\n')[-1]
    return re.sub(r'.+https?://luyencode\.net/problem/([^)]+).+', r'\1', body)


if __name__ == '__main__':
    # comment_urls = get_all_comment_from_issue('https://api.github.com/repos/luyencode/comments/issues/9')
    activity_logs = []
    comment_urls = get_all_issue_comment_from_repo()
    for url in comment_urls:
        data = get_comment_detail(url)
        if is_spoiler_comment(data['body']):
            issue_id = re.sub(r'.+/issues/(\d+)#.+', r'\1', data['html_url'])
            problem_id = get_problem_id(issue_id)
            username = data['user']['login']
            oke = delete_comment(data['url'])
            if oke:
                body = config.TEMPLATE_SPOILER.format(username, problem_id, problem_id, data['body'])
            if oke:
                activity_logs.append(body)
                print('=> ' + body)
            else:
                print('Bugs bugs bugs')
                exit()
    save_checkpoint()
    if make_issue_comment(config.ADMIN_ISSUE_ID, '\n'.join(activity_logs) + config.TEMPLATE_DOCUMENT):
        print('All done!')
    else:
        print('All done but log error!')
