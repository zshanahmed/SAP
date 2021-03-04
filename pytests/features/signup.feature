# Created by eliasshaeffer at 3/1/21
Feature: Sign up
  Way for new allies to sign up for the service

  Scenario: I click on the signup button
    Given I go to home page
    When I click the button with id: "sign-up"
    Then I should be on page with url: "http://127.0.0.1:8000/sign-up/"

    Scenario: I try and create an account with an existing username
    Given I have navigated to sign-up page
    When I fill in "iba_admin1" into element: "new_username"
    And I fill in "name" into element: "firstName"
    And I fill in "lastName" into element: "lastName"
    And I fill in "iba_sep_1" into element: "new_password"
    And I fill in "iba_sep_1" into element: "repeat_password"
    And I click the radio button with id: "undergradCheck"
    And I fill in the undergrad form
    Then I should see text: "Account can not be created because username already exists"
    And I should be on page with url: "http://127.0.0.1:8000/sign-up/"


  Scenario: I fill out the form and submit a undergraduate student
    Given I have navigated to sign-up page
    When I fill in "hawk1" into element: "new_username"
    And I fill in "name" into element: "firstName"
    And I fill in "lastName" into element: "lastName"
    And I fill in "iba_sep_1" into element: "new_password"
    And I fill in "iba_sep_1" into element: "repeat_password"
    And I click the radio button with id: "undergradCheck"
    And I fill in the undergrad form
    Then I should see text: "Account created"
    And I should be on page with url: "http://127.0.0.1:8000/"
    And be able to login with username "hawk1", and password "iba_sep_1"

  Scenario: I fill out the form and submit as a graduate student
    Given I have navigated to sign-up page
    When I fill in "hawk2" into element: "new_username"
    And I fill in "name" into element: "firstName"
    And I fill in "lastName" into element: "lastName"
    And I fill in "iba_sep_1" into element: "new_password"
    And I fill in "iba_sep_1" into element: "repeat_password"
    And I click the radio button with id: "gradCheck"
    And I fill in the grad form
    Then I should see text: "Account created"
    And I should be on page with url: "http://127.0.0.1:8000/"
    And be able to login with username "hawk2", and password "iba_sep_1"

  Scenario: I fill out the form and submit as a staff member
    Given I have navigated to sign-up page
    When I fill in "hawk3" into element: "new_username"
    And I fill in "name" into element: "firstName"
    And I fill in "lastName" into element: "lastName"
    And I fill in "iba_sep_1" into element: "new_password"
    And I fill in "iba_sep_1" into element: "repeat_password"
    And I click the radio button with id: "staffCheck"
    And I fill in staff form
    Then I should see text: "Account created"
    And I should be on page with url: "http://127.0.0.1:8000/"
    And be able to login with username "hawk3", and password "iba_sep_1"

  Scenario: I fill out the form and submit as a faculty
    Given I have navigated to sign-up page
    When I fill in "hawk4" into element: "new_username"
    And I fill in "name" into element: "firstName"
    And I fill in "lastName" into element: "lastName"
    And I fill in "iba_sep_1" into element: "new_password"
    And I fill in "iba_sep_1" into element: "repeat_password"
    And I click the radio button with id: "facultyCheck"
    And I fill in faculty form
    Then I should see text: "Account created"
    And I should be on page with url: "http://127.0.0.1:8000/"
    And be able to login with username "hawk4", and password "iba_sep_1"