import { render, screen } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import QueueColumn from '../QueueColumn.svelte';

describe('QueueColumn', () => {
  it('renders title and empty state by default', async () => {
    const { container } = render(QueueColumn, { props: { title: 'Test Queue', files: [] } });
    expect(screen.getByRole('heading', { level: 2, name: 'Test Queue' })).toBeInTheDocument();
    expect(screen.getByText('Empty')).toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('renders items when files are provided', async () => {
    render(QueueColumn, { props: { title: 'Queue', files: ['a.pdf', 'b.pdf'] } });
    expect(screen.getByText('a.pdf')).toBeInTheDocument();
    expect(screen.getByText('b.pdf')).toBeInTheDocument();
  });
});
