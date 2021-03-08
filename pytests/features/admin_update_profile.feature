Feature: Admin Update Profile

  As an IBA admin
  So that I can update my profile
  I want to goto update profile page and update username and email

  Scenario: Update username with non-existing username and update email
    Given I have logged in with username iba_admin and password iba_sep_1
    When I goto update profile page 
    And I fill out new username iba_admin_changed and email 'admin@admin.com' and submit
    Then I should see the message saying Profile Updated
    And I should change username iba_admin_changed back to old username iba_admin and the page shows Profile Updated

  Scenario: Update username with existing username and update email
    Given I have logged in with username iba_admin and password iba_sep_1
    When I goto update profile page 
    And I fill out new username iba_admin and email 'admin@admin.com' and submit
    Then I should see the message saying Could not Update Profile
    And I should change username iba_admin back to old username iba_admin and the page shows Could not Update Profile