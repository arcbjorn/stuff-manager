#!/bin/bash

import os
from datetime import datetime

import requests
from requests.exceptions import HTTPError

path = os.path.dirname(os.path.realpath(__file__))

# creating directory with employees
if not os.path.exists('tasks'):
    os.makedirs('tasks')

# REST GET API
todos_url = 'https://json.medrating.org/todos'
users_url = 'https://json.medrating.org/users'

# response - data lists in JSON format
users_list = []
todos_list = []

# data requests
try:
    users_res = requests.get(users_url)
    users_res.raise_for_status()
except HTTPError:
    print('Could not download User data from', users_res.url)
else:
    print(users_res.url, 'downloaded successfully')
    users_list = users_res.json()

try:
    todos_res = requests.get(todos_url)
    todos_res.raise_for_status()
except HTTPError:
    print('Could not download Todo data from', todos_res.url)
else:
    print(todos_res.url, 'downloaded successfully')
    todos_list = todos_res.json()


# filtering Todos by user id and completion
def get_completed_by_id(todos, current_user_id):
    completed = []
    for todo in todos:
        if todo.get('userId') == current_user_id:
            if todo['completed']:
                completed.append(todo['title'])
    return completed


# filtering Todos by user id and INcompletion
def get_uncompleted_by_id(todos, current_user_id):
    uncompleted = []
    for todo in todos:
        if todo.get('userId') == current_user_id:
            if not todo['completed']:
                uncompleted.append(todo['title'])
    return uncompleted


def find_user_object(username):
    for user_obj in users_list:
        if user_obj.get('username') == username:
            return user_obj


def write_in_file(username):
    file = os.path.join('tasks', username + '.txt')
    f = open(file, 'w+')
    user = find_user_object(username)

    date = datetime.today().strftime('%d.%m.%Y %H:%M')
    f.write(user['name'] + ' <' + user['email'] + '> ' + date + '\n')
    f.write(user['company']['name'] + '\n')
    f.write('\n')

    f.write('Завершённые задачи:' + '\n')
    user_completed_tasks = get_completed_by_id(todos_list, user['id'])
    if not len(user_completed_tasks):
        print(f'{username} has no completed tasks.')
    for task in user_completed_tasks:
        line_task = task[0:50] + '...' if len(task) > 50 else task
        f.write(line_task + '\n')

    f.write('\n' + 'Оставшиеся задачи:' + '\n')
    user_uncompleted_tasks = get_uncompleted_by_id(todos_list, user['id'])
    if not len(user_uncompleted_tasks):
        print(f'{username} has no tasks left to do.')
    for task in user_uncompleted_tasks:
        line_task = task[0:50] + '...' if len(task) > 50 else task
        f.write(line_task + '\n')
    f.close()


def make_file(username):
    if os.path.isfile('tasks/' + username + '.txt'):
        old_name = os.path.join('tasks', username + '.txt')
        created_at = os.stat(old_name).st_ctime
        date = datetime.fromtimestamp(created_at).strftime('_%Y-%m-%dT%H:%M')
        username_date = username + date
        new_name = os.path.join('tasks', username_date + '.txt')
        os.rename(old_name, new_name)
        write_in_file(username)
        print(f"Updated {username}'s tasks.")
    else:
        write_in_file(username)
        print(f'New user added to database: {username}.')


for user_model in users_list:
    if len(user_model) > 1:
        make_file(user_model['username'])
    else:
        print('There is no user with this id.')
