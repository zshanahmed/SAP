Feature: Admin Edit Ally Profile

  As an IBA admin
  So that I can edit Ally profile
  I want to goto Edit profile page from table on dashboard

  Scenario: Edit Ally
    Given I have logged in with username iba_admin and password iba_sep_1
    When I click on edit button correspoding to a row on table
    Then I should see the edit profile page with information of that Ally
