import { render } from '@testing-library/svelte';
import Layout from '../+layout.svelte';

describe('Layout', () => {
  it('renderiza sem erros', () => {
    const { container } = render(Layout, { props: { children: () => 'Conteúdo' } });
    expect(container).toBeTruthy();
  });
});
