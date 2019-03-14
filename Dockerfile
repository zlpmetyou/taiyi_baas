FROM hyperledger/cello-baseimage:latest

COPY ./ /app/
COPY /celery.conf /etc/supervisor/conf.d/
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN	cd /app/ && \
	pip install -r requirements.txt && \
	rm -rf /tmp/cello

CMD /etc/init.d/supervisor start && if [ "$DEBUG" = "True" ]; then python dashboard.py ; else gunicorn -w 2 --worker-class eventlet -b 0.0.0.0:8080 dashboard:app ;fi