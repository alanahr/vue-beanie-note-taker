import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CommentPanel from '../components/CommentPanel.vue'

describe('CommentPanel', () => {
  it('renders the comment input row', () => {
    const wrapper = mount(CommentPanel, {
      props: {
        editor: null,
        json: { type: 'doc', content: [] },
      },
    })
    expect(wrapper.find('.comment-feature').exists()).toBe(true)
    expect(wrapper.find('.comment-input').exists()).toBe(true)
  })

  it('shows the Add Comment button', () => {
    const wrapper = mount(CommentPanel, {
      props: {
        editor: null,
        json: { type: 'doc', content: [] },
      },
    })
    const btn = wrapper.find('.comment-add-btn')
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toContain('Add Comment')
  })

  it('disables Add Comment when no text is entered', () => {
    const wrapper = mount(CommentPanel, {
      props: {
        editor: null,
        json: { type: 'doc', content: [] },
      },
    })
    expect(wrapper.find('.comment-add-btn').attributes('disabled')).toBeDefined()
  })

  it('starts with the comment panel hidden', () => {
    const wrapper = mount(CommentPanel, {
      props: {
        editor: null,
        json: { type: 'doc', content: [] },
      },
    })
    expect(wrapper.find('.comment-panel').exists()).toBe(false)
  })

  it('toggles the comment panel open and closed', async () => {
    const wrapper = mount(CommentPanel, {
      props: {
        editor: null,
        json: { type: 'doc', content: [] },
      },
    })
    const toggleBtn = wrapper.find('.comment-toggle-btn')
    expect(toggleBtn.text()).toContain('Show')

    await toggleBtn.trigger('click')
    expect(wrapper.find('.comment-panel').exists()).toBe(true)
    expect(wrapper.find('.comment-toggle-btn').text()).toContain('Hide')

    await wrapper.find('.comment-toggle-btn').trigger('click')
    expect(wrapper.find('.comment-panel').exists()).toBe(false)
  })

  it('shows the empty state message when there are no comments', async () => {
    const wrapper = mount(CommentPanel, {
      props: {
        editor: null,
        json: { type: 'doc', content: [] },
      },
    })
    await wrapper.find('.comment-toggle-btn').trigger('click')
    expect(wrapper.find('.comment-empty').exists()).toBe(true)
    expect(wrapper.find('.comment-empty').text()).toContain('No comments yet')
  })
})
