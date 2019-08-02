

def run_user_playlist(event, context):

    import base64

    name = base64.b64decode(event['data']).decode('utf-8')
    username = event['attributes']['username']

    print(f'{username} - {name}')

    from spotframework.google.run_user_playlist import run_user_playlist as run

    run(username, name)
