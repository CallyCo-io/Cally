const Configuration = {
    extends: ['@commitlint/config-conventional'],
    rules: {
      'subject-case': [1, 'never'],
    },
    helpUrl: 'https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines',
  }

  module.exports = Configuration
