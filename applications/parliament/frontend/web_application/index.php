<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Ai Parliament</title>
    <link rel="stylesheet" href="style.css" />
  </head>
  <body class="dark-theme">
    <div id="google_translate_element"></div>

    <div class="header">
    <img width="280" height="70" src="https://pavis.iit.it/image/layout_set_logo?img_id=1459610&t=1714401579818">
      <div class="language-selector">
        <label for="languageSelect">Scegli la lingua dell'assistente:</label>
        <select id="languageSelect">
          <option value="it">Italian</option>
          <option value="en">English</option>
          <option value="de">German</option>
          <option value="fr">French</option>
          <option value="es">Spanish</option>
          <option value="pt">Portuguese</option>
          <option value="nl">Dutch</option>
          <option value="pl">Polish</option>
          <option value="ro">Romanian</option>
          <option value="hu">Hungarian</option>
          <option value="cs">Czech</option>
          <option value="sk">Slovak</option>
          <option value="bg">Bulgarian</option>
          <option value="el">Greek</option>
          <option value="lt">Lithuanian</option>
          <option value="lv">Latvian</option>
          <option value="et">Estonian</option>
          <option value="fi">Finnish</option>
          <option value="sv">Swedish</option>
          <option value="da">Danish</option>
          <option value="hr">Croatian</option>
          <option value="sl">Slovenian</option>
          <option value="ga">Irish</option>
          <option value="mt">Maltese</option>
          <option value="cy">Welsh</option>
          <option value="gd">Gaelic</option>
        </select>
      </div>
      <!--<div class="theme-switcher">
        <div class="theme-switcher">
          <button id="themeToggle">Switch Theme</button>
        </div>
      </div>-->
    </div>
    <h1>webtv.camera.it Assistant</h1>

    <h2>
      Questo assistente è in grado di fornire informazioni su video e documenti
      relativi al Parlamento Italiano. Scegli una lingua e seleziona un documento da esplorare!
    </h2>

    <div class="image-grid"></div>
    <script
      type="text/javascript"
      src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"
    ></script>
    <script src="script.js"></script>

    <script>
      var language = "it"; // Default language

      const imageGrid = document.querySelector(".image-grid");

      <?php include 'content_loader.php'; ?>

      // Function to update image links and descriptions
      function updateImageLinksAndDescriptions(lang) {
        imageGrid.innerHTML = ""; // Clear the grid

        images.forEach((image) => {
          const aTag = document.createElement("a");
          aTag.href = image.link + lang; // Append the selected language to the link
          aTag.target = "_blank";
          aTag.style.textDecoration = "none"; // Optional: Removes underline from the links

          const imgTag = document.createElement("img");
          imgTag.src = image.src;
          imgTag.alt = image.alt;
          imgTag.style.width = "100%"; // Ensure image fits container, adjust as needed

          // Create a paragraph element for the description
          const descriptionTag = document.createElement("p");
          descriptionTag.textContent = image.description;
          // Get the current color style from the body, which reflects the current theme
          const currentColor = getComputedStyle(document.body).color;

          // Apply the color to your descriptionTag
          descriptionTag.style.color = currentColor;
          // Append the image and description to the anchor tag
          aTag.appendChild(imgTag);
          aTag.appendChild(descriptionTag); // Append description under the image

          imageGrid.appendChild(aTag);
        });
      }

      // Initially load images with descriptions and the default language
      updateImageLinksAndDescriptions(language);

      // Update image links and descriptions when the selected language changes
      document
        .getElementById("languageSelect")
        .addEventListener("change", function () {
          language = this.value;
          updateImageLinksAndDescriptions(language); // Refresh the grid with the new language and descriptions
        });

      // Theme switcher
      const themeToggle = document.getElementById("themeToggle");
      themeToggle.addEventListener("click", function () {
        document.body.classList.toggle("dark-theme");
        // Update the description text color based on the current theme
        const currentColor = getComputedStyle(document.body).color;
        const descriptionTags = document.querySelectorAll("p");
        descriptionTags.forEach((descriptionTag) => {
          descriptionTag.style.color = currentColor;
        });
      });
    </script>
  </body>
</html>
