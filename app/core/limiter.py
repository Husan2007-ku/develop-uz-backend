from slowapi import Limiter
from slowapi.util import get_remote_address

# Bitta umumiy limiter — main.py va routes fayllari shu yerdan import qiladi
limiter = Limiter(key_func=get_remote_address)
