from Python_lxf.awesomepython3webapp.www import orm
from Python_lxf.awesomepython3webapp.www.models import User, Blog, Comment
import asyncio

async def test(loop):
    await orm.create_pool(loop, host='127.0.0.1', port=3306,
                          user='www-data', password='www-data', db='awesome')
    u = User(name='Test', email='test@example.com', passwd='12345', image='about:blank', id='000')
    await u.save()

async def find(loop):
    await  orm.create_pool(loop, user='www-data', password='www-data', db='awesome')
    rs = await User.findAll()
    print('find test: %s' % rs)

loop = asyncio.get_event_loop()
loop.run_until_complete(find(loop))
loop.run_forever()