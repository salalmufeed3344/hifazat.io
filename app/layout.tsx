import './globals.css';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Hifazat — Pakistan AI Defence Suite',
  description: 'Protect your photo, voice and video before you post them. Prove what was real if a fake circulates. Urdu-first, free, private by design.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site">
          <div className="wrap">
            <Link className="brand" href="/">Hifazat <span>· حفاظت</span></Link>
            <nav>
              <Link href="/nishan">Nishan</Link>
              <Link href="/awaaz">Awaaz</Link>
              <Link href="/tainted">Tainted Video</Link>
              <Link href="/mirage">MIRAGE</Link>
            </nav>
          </div>
        </header>
        <main className="wrap">{children}</main>
        <footer className="wrap">
          Protection is friction + evidence, not a guarantee. PECA §21: AI-editing someone&apos;s photo into illegal content is a crime in Pakistan. Report: NCCIA 1799.
        </footer>
      </body>
    </html>
  );
}
