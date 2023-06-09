import django
django.setup()  # noqa

from stats.models import Race


if __name__ == '__main__':
    print(Race.objects.filter())