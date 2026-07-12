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
    fireEvent.change(searchInput, { target: { value: 'apple' } });
    
    // The list should show 'Apple' in the sidebar buttons
    const sidebarButtons = screen.getAllByRole('button');
    const appleBtn = sidebarButtons.find(btn => btn.textContent.includes('Apple'));
    expect(appleBtn).toBeDefined();
    
    // "Yes" should not be in the sidebar buttons anymore
    const yesBtn = sidebarButtons.find(btn => btn.textContent.includes('Yes') && !btn.className.includes('header-button'));
    expect(yesBtn).toBeUndefined();
  });
});
