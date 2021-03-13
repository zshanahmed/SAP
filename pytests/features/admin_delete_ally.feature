Feature: Admin Delete Ally Profile

  As an IBA admin
  So that I can delete Ally profile
  I want to goto Ally profile page from table on dashboard

  Scenario: Delete ally profile 
    Given I have logged in with username iba_admin and password iba_sep_1
    When I click on delete button correspoding to a row on table
    Then I should not see the entry against that profile in dashboard