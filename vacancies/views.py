import json

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from amazing_hunting import settings
from vacancies.models import Vacancy, Skill
from vacancies.serializers import VacancyListSerializer, VacancyDetailSerializer, VacancyCreateSerializer


def hello(request):
    return HttpResponse("Hello world")

# @csrf_exempt
# def index(request):
#     if request.method == 'GET':
#         vacancies = Vacancy.objects.all()
#
#         search_text = request.GET["text"]
#         if search_text:
#             vacancies = vacancies.filter(text=search_text)
#
#         responce = []
#         for vacancy in vacancies:
#             responce.append({
#                 "id": vacancy.id,
#                 "text": vacancy.text
#             })
#
#         return JsonResponse(responce, safe=False)
#     elif request.method == 'POST':
#         vacancy_data = json.loads(request.body)
#
#         vacancy = Vacancy()
#         vacancy.text = vacancy_data["text"]
#         vacancy.save()
#
#         return JsonResponse({
#             "id": vacancy.id,
#             "text": vacancy.text
#         })


class VacancyListView(ListView):
    model = Vacancy

    def get(self, request, *args,**kwargs):
        super().get(request, *args, **kwargs)

        search_text = request.GET.get("text", None)
        if search_text:
            self.object_list = self.object_list.filter(text=search_text)

        self.object_list = self.object_list.order_by("text")

        # Пагинация вручную
        # total = self.object_list.count()
        # page_number = request.GET.get("page", 1)
        # offset = (page_number - 1)*settings.TOTAL_ON_PAGE
        #
        # if (page_number - 1)*settings.TOTAL_ON_PAGE < total:
        #     self.object_list = self.object_list[offset: offset + settings.TOTAL_ON_PAGE]
        # else:
        #     self.object_list = self.object_list[offset: total]

        #Сортировка

        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)


        # vacancies = []
        # for vacancy in page_obj:
        #     vacancies.append({
        #         "id": vacancy.id,
        #         "text": vacancy.text
        #     })
        list(map(lambda x: setattr(x, "username", x.user.username if x.user else None), page_obj))
        responce = {
            "items": VacancyListSerializer(page_obj, many=True).data,
            "num_pages": paginator.num_pages,
            "total": paginator.count
        }
        return JsonResponse(responce, safe=False)

class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        vacancy = self.get_object()

        return JsonResponse(VacancyDetailSerializer(vacancy).data)

@method_decorator(csrf_exempt, name="dispatch")
class VacancyCreateView(CreateView):
    model = Vacancy
    fields = ["user", "slug", "text", "status", "created", "skills"]

    def post(self, request, *args, **kwargs):
        vacancy_data = VacancyCreateSerializer(json.loads(request.body))
        if vacancy_data.is_valid():
            vacancy_data.save()
        else:
            return JsonResponse(vacancy_data.errors)

        return JsonResponse(vacancy_data.data)


@method_decorator(csrf_exempt, name="dispatch")
class VacancyUpdateView(UpdateView):
    model = Vacancy
    fields = ["slug", "text", "status","skills"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        vacancy_data = json.loads(request.body)
        self.object.slug=vacancy_data["slug"]
        self.object.text=vacancy_data["text"]
        self.object.status=vacancy_data["status"]

        for skill in vacancy_data["skills"]:
            try:
                skill_obj = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return JsonResponse({"error": "Skill not found"}, status=404)
            self.object.skills.add(skill_obj)

        self.object.save()

        skills_list = list(self.object.skills.all().values_list("name", flat=True))

        return JsonResponse({
            "id": self.object.id,
            "text": self.object.text,
            "slug": self.object.slug,
            "status": self.object.status,
            "created": self.object.created,
            "user": self.object.user_id,
            "skills": skills_list,
        })


@method_decorator(csrf_exempt, name="dispatch")
class VacancyDeleteView(DeleteView):
    model = Vacancy
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)

# def get(request, vacancy_id):
#     if request.method == 'GET':
#         try:
#             vacancy = Vacancy.objects.get(pk=vacancy_id)
#         except Vacancy.DoesNotExist:
#             return JsonResponse({"error": "Not found"}, status=404)
#
#         return JsonResponse({
#             "id": vacancy.id,
#             "text": vacancy.text
#         })

class UserVacancyDetailView(View):
    def get(self, request):
        user_qs = User.objects.annotate(vacancies=Count('vacancy'))

        paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        users = []

        for user in page_obj:
            users.append({
                "id": user.id,
                "name": user.username,
                "vacancies": user.vacancies
            })

        responce = {
            "items": users,
            "num_pages": paginator.num_pages,
            "total": paginator.count,
            "avg": user_qs.aggregate(Avg("vacancies"))
        }

        return JsonResponse(responce)


