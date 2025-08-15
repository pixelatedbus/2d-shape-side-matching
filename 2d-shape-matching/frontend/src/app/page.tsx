'use client';

import { useState, FormEvent } from 'react';

// The API response for a result
interface SearchResult {
  id: number;
  img_name: string;
  score: number;
  img_src: string; // e.g., "images/puzzle1.png"
}

// Define the base URL for the backend API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://shape-matcher-backend-761181960505.asia-southeast2.run.app';

export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(2000);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault(); 
    if (!selectedFile) {
      setError('Please select an image file first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults([]);
    setSearchTime(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('threshold', String(threshold));

    try {
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Something went wrong with the request.');
      }

      const data = await response.json();
      setResults(data.results);
      setSearchTime(data.search_time);

    } catch (err: unknown) { // Use 'unknown' instead of 'any'
      let errorMessage = 'An unknown error occurred';
      
      // Check if the error is an actual Error object
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50 font-sans">
      <div className="w-full max-w-2xl bg-white p-8 rounded-xl shadow-lg border border-gray-200">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
          2D Shape Side Matching
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Form inputs... */}
          <div>
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
              Upload Image
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/png, image/jpeg"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
            />
          </div>
          <div>
            <label htmlFor="threshold" className="block text-sm font-medium text-gray-700">
              Similarity Threshold: <span className="font-semibold text-blue-600">{threshold.toFixed(0)}</span>
            </label>
            <input
              id="threshold"
              type="range"
              min="200"
              max="5000"
              step="100"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !selectedFile}
            className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Searching...' : 'Find Match'}
          </button>
        </form>

        {/* Results Section */}
        <div className="mt-8">
          {isLoading && <p className="text-center text-gray-500">Processing, please wait...</p>}
          {error && <p className="text-center text-red-500 font-medium">Error: {error}</p>}
          
          {searchTime !== null && (
             <p className="text-center text-gray-600 mb-4">
              Search completed in <span className="font-bold text-green-600">{searchTime.toFixed(4)}</span> seconds.
            </p>
          )}

          {results.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Matching Shapes:</h2>
              <ul className="space-y-3">
                {results.map((result) => (
                  <li key={result.id} className="p-3 bg-gray-100 rounded-lg flex items-center space-x-4">
                    {/* Image Display using the static path */}
                    <img
                      src={`${API_BASE_URL}/${result.img_src}`}
                      alt={result.img_name}
                      className="w-16 h-16 object-contain bg-white border border-gray-200 rounded-md"
                      onError={(e) => (e.currentTarget.src = 'https://placehold.co/64x64/eee/ccc?text=Error')}
                    />
                    <div className="flex-grow">
                      <p className="font-medium text-gray-800">{result.img_name}</p>
                    </div>
                    <span className="text-sm font-mono bg-blue-100 text-blue-800 px-2 py-1 rounded-md">
                      Score: {result.score.toFixed(0)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {!isLoading && searchTime !== null && results.length === 0 && (
            <p className="text-center text-gray-500">No matches found below the specified threshold.</p>
          )}
        </div>
      </div>
    </main>
  );
}
