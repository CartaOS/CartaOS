import { render, screen } from '@testing-library/svelte';
import Layout from '../+layout.svelte';

describe.skip('Layout', () => {
  it('renderiza sem erros', () => {
    render(Layout);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
