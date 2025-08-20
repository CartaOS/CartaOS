import { render, screen } from '@testing-library/svelte';
import Page from '../+page.svelte';

describe('Página inicial', () => {
  it('renderiza o título de boas-vindas', () => {
    render(Page);
    expect(screen.getByRole('heading', { name: /cartaos/i })).toBeInTheDocument();
  });
});
