FROM python as django-exchange
WORKDIR /Exchange
COPY . .
RUN python -m venv ./dockervenv
RUN source ./dockervenv/bin/activate
RUN pip install -r req.txt
RUN pip install gunicorn
CMD gunicorn --workers=1 -b 0.0.0.0:8000 'Exchange.wsgi:application'
EXPOSE 8000
