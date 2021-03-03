# Created by eliasshaeffer at 3/1/21
Feature: Sign up
  Way for new allies to sign up for the service

  Scenario: I click on the signup button
    Given I go to home page
    When I click the button with id: "sign-up"
    Then I should be on page with url: "http://127.0.0.1:8000/sign-up/"

  Scenario: I have navigated to the sign-up page and I've selected undergrad as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "undergradCheck"
    Then I should see element with id: "undergradRadios"

  Scenario: I have navigated to the sign-up page and I've selected grad as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "gradCheck"
    Then I should see element with id: "lab_shadowing"

  Scenario: I have navigated to the sign-up page and I've selected faculty as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "facultyCheck"
    Then I should see element with id: "current_openings"

  Scenario: I have navigated to the sign-up page and I've selected staff as University status
    Given I have navigated to sign-up page
    When I click the radio button with id: "staffCheck"
    Then I should see element with id: "how_serve"

#  Scenario: I try and create an account with an existing username
#    Given I have navigated to sign-up page
#    And I fill in "iba_admin1" into element: "new_username"
#    And I fill in "iba_sep_1" into element: "new_password"
#    And I fill in "iba_sep_1" into element: "repeat_password"
#    When I fill out the form and press submit
#    Then I should see text: "Account was not created because username exists"
#    Then I should be on page with url: "http://127.0.0.1:8000/"
#
#
#  Scenario: I forget to fill out something as a undergraduate student
#    Given I have navigated to sign-up page
#
#  Scenario: I forget to fill out something as a graduate student
#    Given I have navigated to sign-up page
#
#  Scenario: I forget to fill out something as a staff member
#    Given I have navigated to sign-up page
#
#  Scenario: I forget to fill out something as a faculty
#    Given I have navigated to sign-up page
#
#  Scenario: I fill out the form and submit a undergraduate student
#    Given I have navigated to sign-up page
#
#  Scenario: I fill out the form and submit as a graduate student
#    Given I have navigated to sign-up page
#
#  Scenario: I fill out the form and submit as a staff member
#    Given I have navigated to sign-up page
#
#  Scenario: I fill out the form and submit as a faculty
#    Given I have navigated to sign-up page