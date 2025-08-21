import { render, screen } from '@testing-library/svelte';
import QueueColumn from '../QueueColumn.svelte';

describe('QueueColumn', () => {
  test('renders files list', async () => {
    render(QueueColumn as any, { props: { title: 'Triage', files: ['a.pdf', 'b.pdf'] } });
    expect(await screen.findByText('a.pdf')).toBeInTheDocument();
    expect(await screen.findByText('b.pdf')).toBeInTheDocument();
    expect(screen.getByText('Triage')).toBeInTheDocument();
  });

  test('renders Empty when no files', async () => {
    render(QueueColumn as any, { props: { title: 'Empty List', files: [] } });
    expect(await screen.findByText('Empty')).toBeInTheDocument();
  });
});
