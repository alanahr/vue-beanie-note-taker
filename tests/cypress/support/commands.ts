/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      clearEditor(): Chainable<void>
      typeIntoEditor(text: string): Chainable<void>
    }
  }
}

Cypress.Commands.add('clearEditor', () => {
  cy.get('.ProseMirror').first().click().then(($el) => {
    cy.wrap($el).type('{selectall}{backspace}')
  })
})

Cypress.Commands.add('typeIntoEditor', (text: string) => {
  cy.get('.ProseMirror').first().click().type(text)
})
