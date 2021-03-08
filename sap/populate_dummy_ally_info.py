# python manage.py shell
# copy paste the following commands to populate dummy data
from sap.models import Ally
from django.contrib.auth.models import User

'''user_1 = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glass onion',
                                 first_name='John',
                                 last_name='Beatles')
'''

user_2 = User.objects.create_user(username='john2',
                                  email='jlennon2@beatles.com',
                                  password='glass onion',
                                  first_name='John',
                                  last_name='Beatles2')
'''
user_3 = User.objects.create_user(username='john3',
                                 email='jlennon3@beatles.com',
                                 password='glass onion',
                                 first_name='John',
                                 las_name='Beatles3'
                                 )

user_4 = User.objects.create_user(username='john4',
                                 email='jlennon4@beatles.com',
                                 password='glass onion',
                                 first_name='John',
                                 las_name='Beatles4')

user_5 = User.objects.create_user(username='john5',
                                 email='jlennon5@beatles.com',
                                 password='glass onion',
                                 first_name='John',
                                 las_name='Beatles5')
'''
# Required fields: hawk_id, user_type, works_at, year, major

'''
ally_1 = Ally.objects.create(user = user_1, hawk_id = 'hawk1', user_type = 'student', works_at = 'College of Engineering', year = 'first',
                             major = 'Computer Science')
'''

ally_2 = Ally.objects.create(user=user_2, hawk_id='hawk2', user_type='student', works_at='College of Engineering', year='second',
                             major='Biology')

# New data
user = User.objects.create_user(username='amahmood1',
                                email='amahmood1@uiowa.edu',
                                password='amahmood1',
                                first_name='Asad',
                                last_name='Mahmood')

ally = Ally.objects.create(
    user=user,
    hawk_id='amahmood1',
    user_type='Student',
    works_at='College of Liberal Arts',
    area_of_research='Application of ML/DL on User Privacy',
    description_of_research_done_at_lab='Worked on Authorship Obfuscation',
    people_who_might_be_interested_in_iba='Zeeshan',
    how_can_science_ally_serve_you='Help in finding internship',
    year='2021',
    major='Computer Science'
)
