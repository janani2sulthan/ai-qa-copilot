Feature: Login

  Scenario: Login with valid credentials
    Given I open the login page
    When I enter valid credentials
    And I click login
    Then I should see the dashboard

  Scenario: Login with invalid credentials
    Given I open the login page
    When I enter invalid credentials
    And I click login
    Then I should see an error message
