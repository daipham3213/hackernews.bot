START_MSG = r"""
Hi! I'm Hacker News Bot.
I can help you find the latest news from Hacker News.
Just send me a command and I'll do my best to assist you.
You can use the following commands:

`\/start`
`\/top_stories`
`\/item <item_id>`
"""

INVALIDCMD_MSG = """
I'm sorry, but I don't understand that command.
Please use one of the following commands:

`/top_stories`
`/item <item_id>`
"""

STORY_TEMPLATE = """
🔗 <a href="{url}">{title}</a>

{text}

✍️ By: {by}
👍 Score: {score}
💬 Comments: {descendants}
🕒 Time: {time}
"""
