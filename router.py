# Маршрутизация
from public.method import Router
from views.client import *
from views.admin import *

router = Router()
router.add_route('r/index', Index, 'index')
router.add_route('r/instruction', Index, 'instruction')
router.add_route('r/channel', Channel, 'index')
router.add_route('r/channel_fleet', Channel, 'fleet_info')
router.add_route('r/channel_apply', Channel, 'add_fleet')
router.add_route('r/channel_submit', Channel, 'submit_fleet')
router.add_route('r/del_msg', User, 'backReview')

router.add_route('a/admin', Admin, 'index')
router.add_route('a/init_menu', Admin, 'initialization')
router.add_route('a/config', Admin, 'config')
router.add_route('a/edit_config', Admin, 'modifBot')
router.add_route('a/reject_words', Admin, 'reviewRejectionWords')
router.add_route('a/add_reject_word', Admin, 'delReviewRejectionWords')
router.add_route('a/del_reject_word', Admin, 'delReviewRejectionWords')

router.add_route('a/ad', Advertising, 'index')
router.add_route('a/ad_input', Advertising, 'adInput')
router.add_route('a/del_ad', Advertising, 'delAdvertising')

router.add_route('a/car', Car, 'index')
router.add_route('a/car_input', Car, 'inputBot')
router.add_route('a/car_channel', Car, 'channel_car')
router.add_route('a/car_fleet', Car, 'channel_fleet_info')
router.add_route('a/car_ch_info', Car, 'channel_info')
router.add_route('a/car_ch_state', Car, 'channel_fleet_state')
router.add_route('a/car_toggle', Car, 'downGroup')
router.add_route('a/car_ban', Car, 'banGroup')


router.add_route('a/review_pass', Review, 'passReview')
router.add_route('a/pick_fleet', Review, 'pickFleet')
router.add_route('a/assign_fleet', Review, 'assignFleet')
router.add_route('a/review_reject', Review, 'rejectReview')
router.add_route('a/review_reason', Review, 'rejectReason')
router.add_route('a/custom_reason', Review, 'inputBot')
router.add_route('a/review_back', Review, 'rejectBack')
router.add_route('a/review_ban', Review, 'banGroup')
router.add_route('a/review_down', Review, 'downGroup')

router.add_route('a/group', Group, 'index')
router.add_route('a/group_input', Group, 'inputBot')
router.add_route('a/group_info', Group, 'groupInfo')
router.add_route('a/group_ban', Group, 'banGroup')

router.add_route('a/user', User, 'getUser')  # Выборка пользователей
router.add_route('a/user_input', User, 'inputBot')
router.add_route('a/user_info', User, 'userInfo')  # Профиль пользователя
router.add_route('a/set_admin', User, 'setAdmin')
router.add_route('a/ban_user', User, 'banUser')
router.add_route('a/back', User, 'backReview')
router.add_route('a/del_msg', User, 'backReview')

router.add_route('a/bot_bl', BotBlacklist, 'index')
router.add_route('a/bot_bl_input', BotBlacklist, 'botInput')
router.add_route('a/del_bot_bl', BotBlacklist, 'delBotBlacklist')



