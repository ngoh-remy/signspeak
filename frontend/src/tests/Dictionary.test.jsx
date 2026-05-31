import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Dictionary from '../pages/Dictionary';
import * as AuthContextModule from '../context/AuthContext';

describe('Dictionary Component', () => {
  it('renders correctly with default English language', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({ language: 'en', user: null });
    render(<Dictionary />);
    
    // Check for the search input placeholder in English
    expect(screen.getByPlaceholderText(/Search supported signs/i)).toBeInTheDocument();
  });

  it('translates UI to French when language is fr', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({ language: 'fr', user: null });
    render(<Dictionary />);
    
    // Check for the search input placeholder in French
    expect(screen.getByPlaceholderText(/Rechercher des signes/i)).toBeInTheDocument();
  });

  it('filters dictionary items based on search query', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({ language: 'en', user: null });
    render(<Dictionary />);
    
    // Find the search input and type 'thank you'
    const searchInput = screen.getByPlaceholderText(/Search supported signs/i);
    fireEvent.change(searchInput, { target: { value: 'thank you' } });
    
    // The list should show 'Thank You' in the sidebar buttons
    // The sidebar list items have the class dict-list-btn, we can check by Role or by Text
    const sidebarButtons = screen.getAllByRole('button');
    const thankYouBtn = sidebarButtons.find(btn => btn.textContent.includes('Thank You'));
    expect(thankYouBtn).toBeDefined();
    
    // "Hello" should not be in the sidebar buttons anymore
    const helloBtn = sidebarButtons.find(btn => btn.textContent.includes('Hello') && !btn.className.includes('header-button')); // avoid catching arbitrary header buttons if any
    expect(helloBtn).toBeUndefined();
  });
});
