function yesnoCheck(div_name) {
	document.getElementById('contents').innerHTML = document.getElementById(div_name).innerHTML;
}

    function addRadioOptions(div_id, field_list)
    {
        x = document.getElementById(div_id);
        console.log(x.innerHTML);
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
    console.log(x.innerHTML);
    var i, field;

    for (i=0; i<field_list.length; i++)
    {
        field_id = field_list[i].replace(/\s+/g, '').toLowerCase();
        x.innerHTML += "<input type=\"checkbox\" value=\""+field_list[i]+"\" name=\""+div_id+"\" id=\""+field_id+"\"> \
        <label class=\"form-check-label\" for=\""+div_id+"\">"+field_list[i]+"</label><br/>"  
    }
}

addRadioOptions('studentsInterestedRadios', ['Yes', 'No'])
addRadioOptions('undergradRadios', ['Freshman', 'Sophomore', 'Junior', 'Senior'])
addRadioOptions('interestRadios', ['Yes', 'No'])
addRadioOptions('experienceRadios', ['Yes', 'No'])
addRadioOptions('interestedRadios', ['Yes', 'No'])
addRadioOptions('beingMentoredRadios', ['Yes', 'No'])

addRadioOptions('openingRadios', ['Yes', 'No'])
addCheckBoxes('stemCheckboxes',['Biochemistry', 'Bioinformatics', 'Biology', 'Biomedical Engineering','Chemical Engineering','Chemistry','Computer Science and Engineering','Environmental Science','Health and Human Physiology','Mathematics','Microbiology','Neuroscience','Nursing','Physics','Psychology'])
addCheckBoxes('idUnderGradCheckboxes',['First generation college-student','Rural', 'Low-income','Underrepresented racial/ethnic minority', 'Disabled', 'Transfer student', 'LGBTQ'])
addCheckBoxes('mentoringCheckboxes',['First generation college-student','Rural','Underrepresented racial/ethnic minority', 'Disabled', 'Transfer student', 'LGBTQ'])
addRadioOptions('volunteerRadios',['Yes','No'])
addRadioOptions('trainingRadios',['Yes','No'])
addRadioOptions('agreementRadios',['Yes','No'])

addCheckBoxes('stemGradCheckboxes',['Biochemistry', 'Bioinformatics', 'Biology', 'Biomedical Engineering','Chemical Engineering','Chemistry','Computer Science and Engineering','Environmental Science','Health and Human Physiology','Mathematics','Microbiology','Neuroscience','Nursing','Physics','Psychology'])
addRadioOptions('mentoringGradRadios',['Yes','No'])
addRadioOptions('mentoringFacultyRadios',['Yes','No'])
addCheckBoxes('mentoringGradCheckboxes',['First generation college-student', 'Low-income','Rural','Underrepresented racial/ethnic minority', 'Disabled', 'Transfer student', 'LGBTQ'])
addRadioOptions('connectingRadios',['Yes','No'])
addRadioOptions('labShadowRadios',['Yes','No'])
addRadioOptions('volunteerGradRadios',['Yes','No'])
addRadioOptions('gradTrainingRadios',['Yes','No'])