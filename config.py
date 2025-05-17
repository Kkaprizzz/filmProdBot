from aiogram import Bot

TOKEN = "7944818466:AAEJKV5FMFRm1Ztw84MCRxD35sVwPxBbUgg"

channels = {
    
}

allowed_users = [
    7028891864,  
    1254138354  
]

async def check_subscription(bot: Bot, user_id: int, channel_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

async def check_all_subscriptions(bot: Bot, user_id: int) -> bool:
    for _, channel_id in channels.items():
        if not await check_subscription(bot, user_id, channel_id):
            return False
    return True