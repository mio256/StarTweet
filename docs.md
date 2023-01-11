# pythonanywhere

```sh
# deploy
$ pa_autoconfigure_django.py --python=3.10 --nuke https://github.com/mio256/StarTweet.git

# set .env
(env) $ vim .env

# set wsgi.py
(env) $ mv startweet/wsgi.py /var/www/mi0256_pythonanywhere_com_wsgi.py
```