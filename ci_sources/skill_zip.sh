shopt -s nullglob
for skillpath in PublishedSkills/*/*/*.install; do
    skillpath=$(dirname "${skillpath}")
    cd "${skillpath}"
    zip -r ../../../$(basename "${skillpath}") .
    cd ../../..
done
