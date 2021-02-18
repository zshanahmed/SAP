# Created by eliasshaeffer at 2/17/21
Feature: Create New IBA Admin
  As an IBA admin
  So that I can spread the work of managing candidates out
  I would like to create another IBA admin account for a different person

  Background:
    Given I login with the following credentials: "iba_admin iba_sep_1"

  Scenario:
    When I navigate to the account settings page
    And I fill in "iba_admin" into element: "id1"
    And I fill in "iba_sep_1" into element: "id2"
    And I click the button with id: "id3"
    Then I should be on the Create IBA Admin Page

  Scenario:
    Given I'm on the Create IBA Admin Page
    When I fill in "iba_admin2" into element: "id1"
    And I fill in "iba_sep_2" into element: "id2"
    And I click the button with id: "id3"
    Then User with username "iba_admin2" and password "iba_sep_2" should be in the database