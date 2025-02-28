import React from 'react';
import styled from 'styled-components';

const InputContainer = styled.div`
  margin-bottom: 1.5rem;
  position: relative;
`;

const Label = styled.label`
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--dark-text);
  font-size: 1rem;
`;

const InputField = styled.input`
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid var(--island-outline);
  border-radius: 8px;
  font-size: 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  box-shadow: 0 3px 0 rgba(0, 0, 0, 0.05);
  color: var(--dark-text);
  
  /* Cel-shading effect */
  box-shadow: inset 0 2px 3px rgba(0, 0, 0, 0.1);
  
  &:focus {
    outline: none;
    border-color: var(--hero-green);
    box-shadow: 0 0 0 3px rgba(21, 117, 69, 0.1), inset 0 2px 3px rgba(0, 0, 0, 0.1);
  }
  
  &::placeholder {
    color: #aaa;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid var(--island-outline);
  border-radius: 8px;
  font-size: 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  min-height: 120px;
  resize: vertical;
  font-family: inherit;
  color: var(--dark-text);
  
  /* Cel-shading effect */
  box-shadow: inset 0 2px 3px rgba(0, 0, 0, 0.1);
  
  &:focus {
    outline: none;
    border-color: var(--hero-green);
    box-shadow: 0 0 0 3px rgba(21, 117, 69, 0.1), inset 0 2px 3px rgba(0, 0, 0, 0.1);
  }
  
  &::placeholder {
    color: #aaa;
  }
`;

const HelpText = styled.small`
  display: block;
  margin-top: 0.5rem;
  color: ${props => props.error ? '#ff6b6b' : '#666'};
  font-size: 0.85rem;
`;

// Wind Waker themed little boat icon that appears when focused
const BoatIcon = styled.span`
  position: absolute;
  right: 10px;
  top: 38px;
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.3s ease, transform 0.3s ease;
  transform: translateX(10px);
  color: var(--hero-green);
  pointer-events: none;
  
  ${InputField}:focus ~ &, ${TextArea}:focus ~ & {
    opacity: 1;
    transform: translateX(0);
  }
  
  &::after {
    content: "⛵";
  }
`;

const Input = ({ 
  label, 
  multiline = false, 
  helperText, 
  error = false, 
  ...props 
}) => {
  return (
    <InputContainer>
      {label && <Label>{label}</Label>}
      {multiline ? (
        <TextArea {...props} />
      ) : (
        <InputField {...props} />
      )}
      <BoatIcon />
      {helperText && <HelpText error={error}>{helperText}</HelpText>}
    </InputContainer>
  );
};

export default Input; 