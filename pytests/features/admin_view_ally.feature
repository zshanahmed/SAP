Feature: Admin View Ally Profile

  As an IBA admin
  So that I can view Ally profile
  I want to goto Ally profile page from table on dashboard

  Scenario: View Ally
    Given I have logged in with username iba_admin and password iba_sep_1
    When I click on view button correspoding to a row on table
    Then I should see the profile page with information of that Ally
