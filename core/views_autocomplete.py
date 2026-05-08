from dal import autocomplete
from core.models import State, City
from django.db.models import Q


class StateAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = State.objects.all()

        if self.q:
            qs = qs.filter(
                Q(name_without_accents__icontains=self.q) | Q(name__icontains=self.q))

        return qs


class CityAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        state = self.request.GET.get('state')
        
        if state:
            qs = City.objects.filter(state=state)
        else:
            qs = City.objects.all()
        
        if self.q:
            qs = qs.filter(
                Q(name_without_accents__icontains=self.q) | Q(name__icontains=self.q))

        return qs
