<?php
// PHP code to generate JavaScript "images" array
//phpinfo();

require 'vendor/autoload.php';

use Stichoza\GoogleTranslate\GoogleTranslate;

function translateText($text, $targetLanguage) {
    try {
        // Crea una nuova istanza di GoogleTranslate
        $tr = new GoogleTranslate();

        // Imposta la lingua di destinazione
        $tr->setTarget($targetLanguage);

        // Traduci il testo
        $translatedText = $tr->translate($text);

        // Restituisci il testo tradotto
        return $translatedText;
    } catch (Exception $e) {
        return 'Error: ' . $e->getMessage();
    }
}

$documentsPath = __DIR__ . '/documents';
$imagesBasePath = 'https://webtv.camera.it/assets/thumbs/flash_7/2024/';
$videoBaseLink = 'https://0.0.0.0:8502/?video_id=';

//echo $documentsPath;

// Scan the documents folder for text files
$files = glob($documentsPath . '/*.txt');

// Start outputting JavaScript
echo 'const images = ['; // Start the images array

foreach ($files as $file) {
    // Extract file info and construct necessary parts
    $fileInfo = pathinfo($file);
    $baseName = str_replace('_merged', '', $fileInfo['filename']);
    $imageSrc = $imagesBasePath . $baseName . '.jpg';
    $videoLink = $videoBaseLink . $baseName;

    // Open the file to read the first line for the title
    $fileHandle = fopen($file, "r");
    $firstLine = fgets($fileHandle);
    fclose($fileHandle);
    
    // Extract title (assuming format "Title: Actual Title")
    $titleParts = explode("Title: ", $firstLine);
    $title = isset($titleParts[1]) ? trim($titleParts[1]) : "No title found";

    // Output this image's data as a JavaScript object
    echo "{";
    echo "src: \"$imageSrc\", ";
    echo "link: \"$videoLink&lang=\", "; // Assume language will be appended dynamically
    echo "alt: \"Description\", "; // You might want to customize this
    echo "description: \"".addslashes(translateText($title,"it"))."\""; // Escape title for JS
    echo "},";
}

echo '];'; // Close the images array
?>
