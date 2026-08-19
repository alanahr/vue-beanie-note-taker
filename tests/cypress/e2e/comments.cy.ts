describe('Comments', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('renders the comment panel area', () => {
    cy.get('.comment-feature').should('be.visible')
  })

  it('shows the comment input field', () => {
    cy.get('.comment-input').should('be.visible')
  })

  it('shows the Add Comment button', () => {
    cy.get('.comment-add-btn').should('be.visible')
    cy.get('.comment-add-btn').should('contain.text', 'Add Comment')
  })

  it('toggles the comments panel open and closed', () => {
    cy.get('.comment-toggle-btn').should('contain.text', 'Show Comments')
    cy.get('.comment-toggle-btn').click()
    cy.get('.comment-toggle-btn').should('contain.text', 'Hide Comments')
    cy.get('.comment-panel').should('be.visible')
    cy.get('.comment-toggle-btn').click()
    cy.get('.comment-toggle-btn').should('contain.text', 'Show Comments')
  })

  it('disables the Add Comment button when no text is entered', () => {
    cy.get('.comment-add-btn').should('be.disabled')
  })

  it('enables the Add Comment button when text is entered', () => {
    cy.get('.comment-input').type('Test comment')
    cy.get('.comment-add-btn').should('not.be.disabled')
  })
})
