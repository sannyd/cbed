import os

import django
import numpy
import pandas

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from cbed.main.models import Level, Section, Question, Answer

Level.objects.get_or_create(id=20, name="MBE xxx")
Level.objects.get_or_create(id=9, name="Essays")
Level.objects.get_or_create(id=10, name="PT")

section_df = pandas.read_csv("data/main_cbed_dbo_Levels.csv").replace(numpy.nan, '', regex=True)
Section.objects.all().delete()
for index, row in section_df.iterrows():
    level_id = row["SectionId"]
    if level_id not in [9, 10]:
        level_id = 8
    video = row["VideoUrl"]
    videos = []
    pdfs = []
    if video and "youtu" in video:
        videos = [video, ]
    else:
        pdfs = [video, ]
    id_ = row["Id"]
    section = Section.objects.create(id=id_, level_id=level_id, youtube_urls=videos, pdf_urls=pdfs,
                                     name=row["LevelName"],
                                     order=id_)
    print(section)

question_df = pandas.read_csv("data/main_cbed_dbo_Questions.csv").replace(numpy.nan, '', regex=True)
Question.objects.all().delete()
for index, row in question_df.iterrows():
    section_id = row["LevelId"]
    content = row["Content"]
    id_ = row["Id"]
    question = Question.objects.create(id=id_, section_id=section_id,
                                       content=content,
                                       order=id_)
    print(question)

answer_df = pandas.read_csv("data/main_cbed_dbo_Answers.csv").replace(numpy.nan, '', regex=True)
Answer.objects.all().delete()
for index, row in answer_df.iterrows():
    content = row["Content"]
    discussion = row["Discussion"]
    correct = row["IsCorrect"]
    question_id = row["QuestionId"]
    id_ = row["Id"]
    answer = Answer.objects.create(id=id_,
                                   is_correct=correct,
                                   content=content,
                                   discussion=discussion,
                                   question_id=question_id,
                                   order=id_)
    print(answer)
