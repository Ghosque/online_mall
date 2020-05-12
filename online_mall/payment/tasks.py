# -*- coding:utf-8 -*-
import logging

from .models import Order
from common_function.get_timestamp import get_now_timestamp

logger = logging.getLogger(__name__)


def handle_unpaid_orders():
    logger.info('Handle Unpaid Orders Start')
    now_timestamp = get_now_timestamp()
    Order.handle_unpaid_data(now_timestamp)
