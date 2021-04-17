function yesnoCheck(div_name) {
	document.getElementById('contents').innerHTML = document.getElementById(div_name).innerHTML;
}

    function addRadioOptions(div_id, field_list)
    {
        x = document.getElementById(div_id);
        var i, field;

        for (i=0; i<field_list.length; i++)
        {
          field_id = field_list[i].replace(/\s+/g, '').toLowerCase();
          x.innerHTML += "<input type=\"radio\" value=\""+field_list[i]+"\" name=\""+div_id+"\" id=\""+field_id+"\" required> \
            <label class=\"form-check-label\" for=\""+div_id+"\">"+field_list[i]+"</label><br/>"
        }
    }

function addCheckBoxes(div_id, field_list)
{
    x = document.getElementById(div_id);
    var i, field;

    for (i=0; i<field_list.length; i++)
    {
        field_id = field_list[i].replace(/\s+/g, '').toLowerCase();
        x.innerHTML += "<input type=\"checkbox\" value=\""+field_list[i]+"\" name=\""+div_id+"\" id=\""+field_id+"\"> \
        <label class=\"form-check-label\" for=\""+div_id+"\">"+field_list[i]+"</label><br/>"  
    }
}

//Undergrad
addRadioOptions('undergradMentoringRadios', ['Yes', 'No'])
addCheckBoxes('identityCheckboxes',['First generation college-student','Rural', 'Low-income','Underrepresented racial/ethnic minority', 'Disabled', 'Transfer student', 'LGBTQ'])
addRadioOptions('undergradYear', ['Freshman', 'Sophomore', 'Junior', 'Senior'])
addRadioOptions('interestLabRadios', ['Yes', 'No'])
addRadioOptions('labExperienceRadios', ['Yes', 'No'])
addRadioOptions('beingMentoredRadios', ['Yes', 'No'])
addRadioOptions('agreementRadios',['Yes','No'])

//Staff-Facul   faculty-Grad
addRadioOptions('connectingWithMentorsRadios', ['Yes', 'No'])
addRadioOptions('studentsInterestedRadios', ['Yes', 'No'])
addRadioOptions('mentoringRadios', ['Yes', 'No'])
addCheckBoxes('mentorCheckboxes',['First generation college-student','Rural', 'Low-income','Underrepresented racial/ethnic minority', 'Disabled', 'Transfer student', 'LGBTQ'])
addRadioOptions('trainingRadios',['Yes','No'])
addRadioOptions('labShadowRadios',['Yes','No'])
addRadioOptions('volunteerRadios',['Yes','No'])
addCheckBoxes('areaOfResearchCheckboxes',
    ['Biochemistry', 'Bioinformatics', 'Biology', 'Biomedical Engineering','Chemical Engineering',
        'Chemistry','Computer Science and Engineering', 'Computer Science',
        'Environmental Science','Health and Human Physiology',
        'Mathematics','Microbiology','Neuroscience','Nursing','Physics','Psychology'])
addRadioOptions('openingRadios', ['Yes', 'No'])
addRadioOptions('mentorTrainingRadios',['Yes','No'])
