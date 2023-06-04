import pytest 
import datetime
from  slackbot.parsing.slackapi import AppMentionData, BlockData, BlockElement, BlockElementData, BlockElementDataType, BlockElementType, BlockType, EventType

@pytest.mark.parametrize("event_in, expected", [
    ({'client_msg_id': '07fc5446-f407-4a08-a215-f75be8cfa0f9', 'type': 'app_mention', 'text': 'hey',
  'user': 'U058V5QTW12', 'ts': '1685890319.156619', 
  'blocks': [
      {'type': 'rich_text', 'block_id': 'qui', 
       'elements': [
           {'type': 'rich_text_section', 
            'elements': [
                {'type': 'user', 'user_id': 'U058V6AG10C'}, 
                {'type': 'text', 'text': ' hey'}]
            }
        ]
     }
  ], 'team': 'T058PNE2HKP', 
            'channel': 'C0595A85N4R', 
            'event_ts': '1685890319.156619'
}, AppMentionData(client_msg_id='07fc5446-f407-4a08-a215-f75be8cfa0f9', type=EventType.APP_MENTION, text='hey', user='U058V5QTW12',
                   ts='1685890319.156619', blocks=[BlockData(type=BlockType.RICH_TEXT, block_id='qui', elements=[BlockElement(type=BlockElementType.RICH_TEXT_SECTION, elements=[BlockElementData(type=BlockElementDataType.USER, user_id='U058V6AG10C', text=None), BlockElementData(type=BlockElementDataType.TEXT, user_id=None, text=' hey')])])], team='T058PNE2HKP', channel='C0595A85N4R', event_ts='1685890319.156619')),
   
])
def test_(event_in, expected):
    
    actual = AppMentionData(**event_in)
    assert actual == expected, repr(actual)
    