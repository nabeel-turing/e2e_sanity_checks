from .chats import fetch_direct_message_thread, find_conversations, get_conversation_details, get_latest_message_with_contact
from .contacts import list_conversations_with_contact, locate_contacts
from .media import dispatch_media_attachment, save_media_from_message, send_voice_recording
from .messages import get_conversation_around_message, post_text_message, query_message_history

_function_map = {
    'dispatch_media_attachment': 'whatsapp.mutations.m01.media.dispatch_media_attachment',
    'fetch_direct_message_thread': 'whatsapp.mutations.m01.chats.fetch_direct_message_thread',
    'find_conversations': 'whatsapp.mutations.m01.chats.find_conversations',
    'get_conversation_around_message': 'whatsapp.mutations.m01.messages.get_conversation_around_message',
    'get_conversation_details': 'whatsapp.mutations.m01.chats.get_conversation_details',
    'get_latest_message_with_contact': 'whatsapp.mutations.m01.chats.get_latest_message_with_contact',
    'list_conversations_with_contact': 'whatsapp.mutations.m01.contacts.list_conversations_with_contact',
    'locate_contacts': 'whatsapp.mutations.m01.contacts.locate_contacts',
    'post_text_message': 'whatsapp.mutations.m01.messages.post_text_message',
    'query_message_history': 'whatsapp.mutations.m01.messages.query_message_history',
    'save_media_from_message': 'whatsapp.mutations.m01.media.save_media_from_message',
    'send_voice_recording': 'whatsapp.mutations.m01.media.send_voice_recording',
}
