# Created by eliasshaeffer at 2/17/21
Feature: Create New IBA Admin
  As an IBA admin
  So that I can spread the work of managing candidates out
  I would like to create another IBA admin account for a different person
  Background: I've logged in to SAP
    Given I've logged in

  Scenario: I enter my credentials into the settings page and create new admin
    When I navigate to the create verification page
    And I fill in "iba_admin" into element: "current_username"
    And I fill in "iba_sep_1" into element: "current_password"
    And I fill in "iba_admin2" into element: "new_username"
    And I fill in "email@uiowa.edu" into element: "new_email"
    And I fill in "iba_sep_2" into element: "new_password"
    And I fill in "iba_sep_2" into element: "repeat_password"
    And I click the button with id: "submit_new_admin"
    Then I should be on page with url: "http://127.0.0.1:8000/dashboard/"
    And User with username "iba_admin2" and password "iba_sep_2" should exist

  Scenario: I enter incorrect credentials into settings page
    When I navigate to the create verification page
    And I fill in "randomUsername12345fajsd" into element: "current_username"
    And I fill in "reallylongpasswordthatimcreatingjustforfun" into element: "current_password"
        And I fill in "iba_admin2" into element: "new_username"
    And I fill in "email@uiowa.edu" into element: "new_email"
    And I fill in "iba_sep_2" into element: "new_password"
    And I fill in "iba_sep_2" into element: "repeat_password"
    And I click the button with id: "submit_new_admin"
    Then I should be on page with url: "http://127.0.0.1:8000/create_iba_admin/"
    And I should see text: "Invalid credentials entered, please try again"