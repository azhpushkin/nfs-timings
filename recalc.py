from stats.models import *
from stats.processing import *

br = BoardRequest.objects.all().order_by('created_at')

for b in br.filter(status=200).values('pk').iterator():
   b = BoardRequest.objects.get(pk=b['pk'])
   print(b, b.created_at)
   process_json(b)
